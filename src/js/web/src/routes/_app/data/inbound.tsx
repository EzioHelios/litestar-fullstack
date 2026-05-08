import { createFileRoute } from "@tanstack/react-router"
import { PlaceholderPage } from "@/components/platform/placeholder-page"

export const Route = createFileRoute("/_app/data/inbound")({
  component: InboundPage,
})

function InboundPage() {
  return <PlaceholderPage eyebrow="数据管理" title="入库管理" />
}

