import { createFileRoute } from "@tanstack/react-router"
import { PlaceholderPage } from "@/components/platform/placeholder-page"

export const Route = createFileRoute("/_app/tasks/crontab")({
  component: CrontabPage,
})

function CrontabPage() {
  return <PlaceholderPage eyebrow="定时任务" title="crontab设置" />
}

