import type { LucideIcon } from "lucide-react"

import { Card, CardContent } from "@/components/ui/card"

type SummaryMetricCardProps = {
  icon: LucideIcon
  label: string
  value: string
  meta: string
}

export function SummaryMetricCard({ icon: Icon, label, value, meta }: SummaryMetricCardProps) {
  return (
    <Card className="h-full">
      <CardContent className="grid min-h-[96px] grid-cols-[44px_minmax(0,1fr)] items-center gap-4 px-5 py-4">
        <div className="flex size-11 items-center justify-center rounded-xl bg-muted text-foreground/80">
          <Icon className="size-5" />
        </div>
        <div className="flex min-w-0 flex-col justify-center gap-2 self-center">
          <div className="truncate text-sm font-medium leading-5 text-muted-foreground">{label}</div>
          <div className="truncate text-[1.5rem] font-semibold leading-[1.05] tracking-tight text-foreground">{value}</div>
          <div className="truncate text-sm leading-5 text-muted-foreground">{meta}</div>
        </div>
      </CardContent>
    </Card>
  )
}
