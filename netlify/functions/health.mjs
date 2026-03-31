export default async (req) => {
  return Response.json({
    status: "ok",
    model_ready: true,
    version: "1.0.0-demo",
    timestamp: new Date().toISOString(),
  });
};

export const config = {
  path: "/health",
};
