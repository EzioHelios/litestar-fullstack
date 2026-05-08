import { createFileRoute } from "@tanstack/react-router"
import { PlaceholderPage } from "@/components/platform/placeholder-page"

export const Route = createFileRoute("/_app/data/video-alarm-events")({
  component: VideoAlarmEventsPage,
})

function VideoAlarmEventsPage() {
  return <PlaceholderPage eyebrow="数据管理" title="视频监控预警事件" />
}

