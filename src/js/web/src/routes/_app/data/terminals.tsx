import { createFileRoute } from "@tanstack/react-router"
import { PlaceholderPage } from "@/components/platform/placeholder-page"

export const Route = createFileRoute("/_app/data/terminals")({
  component: TerminalsPage,
})

function TerminalsPage() {
  return <PlaceholderPage eyebrow="数据管理" title="监控终端" />
}

