import { createFileRoute, Link } from "@tanstack/react-router"
import { z } from "zod"
import { UserSignupForm } from "@/components/auth/user-signup-form"
import { usePublicConfig } from "@/hooks/use-public-config"
import { validateRedirectUrl } from "@/lib/redirect-utils"

export const Route = createFileRoute("/_public/signup")({
  validateSearch: (search) =>
    z
      .object({
        redirect: z.string().optional(),
      })
      .parse(search),
  component: SignupPage,
})

function SignupPage() {
  const search = Route.useSearch()
  const validatedRedirect = validateRedirectUrl(search.redirect)
  const { config } = usePublicConfig()

  return (
    <div className="flex min-h-screen w-full items-center justify-center bg-muted/30 px-4 py-8">
      <div className="mx-auto flex w-full flex-col justify-center space-y-6 sm:w-96">
        <div className="flex flex-col items-center space-y-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/15 text-primary">
            <span className="text-lg font-bold">{config.shortName}</span>
          </div>
          <div className="text-center">
            <h1 className="font-semibold text-xl tracking-tight">创建新账号</h1>
            <p className="mt-1 text-muted-foreground text-sm">填写信息注册账号</p>
          </div>
        </div>

        <div className="rounded-lg border bg-card p-6 shadow-sm">
          <UserSignupForm redirectUrl={validatedRedirect} />
        </div>

        <p className="text-center text-muted-foreground text-sm">
          已有账号？{" "}
          <Link to="/login" className="font-medium text-primary hover:underline">
            立即登录
          </Link>
        </p>
      </div>
    </div>
  )
}
