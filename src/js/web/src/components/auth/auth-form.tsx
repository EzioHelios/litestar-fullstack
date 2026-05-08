import { useRouter, Link } from "@tanstack/react-router"
import { validateRedirectUrl } from "@/lib/redirect-utils"

import { UserLoginForm } from "./user-login-form"

export function AuthForm() {
  const router = useRouter()

  // Get redirect param from URL search params
  const searchParams = new URLSearchParams(router.state.location.searchStr)
  const redirectParam = searchParams.get("redirect")
  const validatedRedirect = validateRedirectUrl(redirectParam)

  return (
    <div className="flex min-h-screen w-full items-center justify-center bg-muted/30 px-4 py-8">
      <div className="mx-auto flex w-full flex-col justify-center space-y-6 sm:w-96">
        <div className="flex flex-col items-center space-y-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/15 text-primary">
            <span className="text-lg font-bold">XT</span>
          </div>
          <div className="text-center">
            <h1 className="font-semibold text-xl tracking-tight">祥泰仓库数据管理平台</h1>
            <p className="mt-1 text-muted-foreground text-sm">请输入账号密码登录系统</p>
          </div>
        </div>

        <div className="rounded-lg border bg-card p-6 shadow-sm">
          <UserLoginForm redirectUrl={validatedRedirect} />
        </div>

        <p className="text-center text-muted-foreground text-sm">
          还没有账号？{" "}
          <Link to="/signup" className="font-medium text-primary hover:underline">
            立即注册
          </Link>
        </p>
      </div>
    </div>
  )
}
