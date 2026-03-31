import { DEMO_GSTINS, scoreGstin } from "./shared.mjs";

export default async (req) => {
  if (req.method !== "POST") {
    return Response.json({ error: "Method not allowed" }, { status: 405 });
  }

  let body;
  try {
    body = await req.json();
  } catch {
    return Response.json(
      { error: "Bad Request", detail: "Invalid JSON body", status_code: 400 },
      { status: 400 }
    );
  }

  const gstin = (body.gstin || "").toUpperCase();
  if (!gstin || gstin.length !== 15) {
    return Response.json(
      { error: "Validation Error", detail: "GSTIN must be 15 characters", status_code: 422 },
      { status: 422 }
    );
  }

  const data = DEMO_GSTINS[gstin];
  if (!data) {
    return Response.json(
      { error: "Not Found", detail: `GSTIN ${gstin} not found in demo data`, status_code: 404 },
      { status: 404 }
    );
  }

  const result = scoreGstin(data);
  return Response.json(result);
};

export const config = {
  path: "/api/v1/score",
  method: "POST",
};
