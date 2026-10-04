import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Rental Housing Law Navigator" },
      { name: "description", content: "Look up which rent, eviction, deposit and screening rules apply to an address in CA, NJ and MA, with cited sources." },
      { property: "og:title", content: "Rental Housing Law Navigator" },
      { property: "og:description", content: "Address-level rental housing rules with cited sources for California, New Jersey and Massachusetts." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: Index,
});

function Index() {
  return (
    <iframe
      src="/navigator/index.html"
      title="Rental Housing Law Navigator"
      className="fixed inset-0 h-screen w-screen border-0"
    />
  );
}
