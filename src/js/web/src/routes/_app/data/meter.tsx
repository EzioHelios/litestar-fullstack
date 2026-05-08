import { createFileRoute } from "@tanstack/react-router"
import { PlaceholderPage } from "@/components/platform/placeholder-page"

export const Route = createFileRoute("/_app/data/meter")({
  component: MeterPage,
})

function MeterPage() {
  return <PlaceholderPage eyebrow="数据管理" title="电表电量" />
}

