import { Badge } from "@/components/ui/badge"

export type CarbonStatus = "draft" | "pending" | "approved" | "rejected" | string | undefined

export function CarbonStatusBadge({ status }: { status: CarbonStatus }) {
  if (status === "approved") return <Badge>已通过</Badge>
  if (status === "pending") return <Badge variant="secondary">待审核</Badge>
  if (status === "rejected") return <Badge variant="destructive">已驳回</Badge>
  return <Badge variant="outline">草稿</Badge>
}

