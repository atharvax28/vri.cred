import { DEMO_GSTINS } from "./shared.mjs";

export default async (req, context) => {
  const url = new URL(req.url);
  const gstin = context.params?.gstin;

  if (gstin) {
    const data = DEMO_GSTINS[gstin.toUpperCase()];
    if (!data) {
      return Response.json(
        { error: "Not Found", detail: `GSTIN ${gstin} not found in demo data`, status_code: 404 },
        { status: 404 }
      );
    }
    // Return detail response (exclude internal fields)
    const { ...detail } = data;
    return Response.json(detail);
  }

  // List all GSTINs
  const gstins = Object.keys(DEMO_GSTINS);
  return Response.json({ gstins, count: gstins.length });
};

export const config = {
  path: ["/api/v1/gstins", "/api/v1/gstins/:gstin"],
};
