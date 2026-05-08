import { createFileRoute } from "@tanstack/react-router"
import { PlaceholderPage } from "@/components/platform/placeholder-page"

export const Route = createFileRoute("/_app/data/outbound")({
  component: OutboundPage,
})

function OutboundPage() {
  return <PlaceholderPage eyebrow="数据管理" title="出库管理" />
}

