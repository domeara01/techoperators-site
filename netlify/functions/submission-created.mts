// Runs automatically after every verified Netlify Forms submission.
// Sends the applicant to Attio: upserts a Person (matched on email), attaches the
// full answers as a note, and optionally adds them to a list.
// Does nothing until ATTIO_API_KEY is set in the site's environment variables.
//
// Env vars (Netlify > Site configuration > Environment variables):
//   ATTIO_API_KEY            required, Attio access token with record + note + list write scopes
//   ATTIO_FOUNDER_LIST       optional, list slug or ID for founder applications
//   ATTIO_MEMBER_LIST        optional, list slug or ID for membership applications

const ATTIO = "https://api.attio.com/v2";

const LABELS: Record<string, string> = {
  first_name: "First name", last_name: "Last name", email: "Email", help_type: "How we can help", startup: "Startup",
  website: "Website", under_represented: "Under-represented founder", deck_url: "Deck",
  stage: "Investment stage", linkedin: "LinkedIn", motivation: "What prompted them to apply",
  angel_before: "Angel invested before", hban_member: "HBAN member",
  investment_intent: "Intends to invest (3 years)", message: "Message", newsletter: "Newsletter opt-in",
};

async function attio(path: string, method: string, body: unknown) {
  const res = await fetch(`${ATTIO}${path}`, {
    method,
    headers: { Authorization: `Bearer ${Netlify.env.get("ATTIO_API_KEY")}`, "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const text = await res.text();
  if (!res.ok) throw new Error(`Attio ${method} ${path} -> ${res.status}: ${text}`);
  return text ? JSON.parse(text) : {};
}

export default async (req: Request) => {
  const key = Netlify.env.get("ATTIO_API_KEY");
  const { payload } = await req.json();
  const form: string = payload?.form_name ?? "";
  const d: Record<string, string> = payload?.data ?? {};

  if (!key) {
    console.log(`ATTIO_API_KEY not set; skipping Attio sync for ${form}`);
    return new Response("skipped");
  }
  if (!["founder-application", "membership-application"].includes(form) || !d.email) {
    return new Response("ignored");
  }

  const first = (d.first_name || "").trim();
  const last = (d.last_name || "").trim();
  const full = [first, last].filter(Boolean).join(" ") || d.email;

  // 1. Person, matched on email so repeat applicants don't create duplicates
  const person = await attio("/objects/people/records?matching_attribute=email_addresses", "PUT", {
    data: { values: {
      email_addresses: [d.email],
      name: [{ first_name: first, last_name: last, full_name: full }],
    } },
  });
  const personId = person?.data?.id?.record_id;

  // 2. Company for founders, matched on website domain
  if (form === "founder-application" && d.website) {
    try {
      const domain = new URL(/^https?:/i.test(d.website) ? d.website : `https://${d.website}`).hostname.replace(/^www\./, "");
      await attio("/objects/companies/records?matching_attribute=domains", "PUT", {
        data: { values: { domains: [domain] } },
      });
    } catch (e) { console.warn("Company upsert failed", e); }
  }

  // 3. Note with every answer, so nothing depends on custom attributes existing in Attio
  const lines = Object.entries(LABELS)
    .filter(([k]) => d[k])
    .map(([k, label]) => `${label}: ${d[k]}`);
  await attio("/notes", "POST", {
    data: {
      parent_object: "people",
      parent_record_id: personId,
      title: form === "founder-application" ? "Founder application (website)" : "Membership application (website)",
      format: "plaintext",
      content: lines.join("\n"),
    },
  });

  // 4. Optional list entry
  const list = form === "founder-application" ? Netlify.env.get("ATTIO_FOUNDER_LIST") : Netlify.env.get("ATTIO_MEMBER_LIST");
  if (list && personId) {
    try {
      await attio(`/lists/${list}/entries`, "PUT", {
        data: { parent_record_id: personId, parent_object: "people", entry_values: {} },
      });
    } catch (e) { console.warn("List entry failed", e); }
  }

  return new Response("ok");
};
