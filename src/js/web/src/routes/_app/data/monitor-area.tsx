import { createFileRoute } from "@tanstack/react-router"
import { PlaceholderPage } from "@/components/platform/placeholder-page"

export const Route = createFileRoute("/_app/data/monitor-area")({
  component: MonitorAreaPage,
})

function MonitorAreaPage() {
  return <PlaceholderPage eyebrow="数据管理" title="监测区域" />
}

