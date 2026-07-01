import { NextResponse } from "next/server";
import { getAdminLogoutUrl } from "@/lib/admin-auth";

export function GET() {
  const logoutUrl = getAdminLogoutUrl();

  if (!logoutUrl) {
    return NextResponse.json(
      {
        ok: false,
        error: "NEXT_PUBLIC_AUTH_URL or NEXT_PUBLIC_BACKEND_URL is not configured.",
      },
      { status: 500 }
    );
  }

  const response = NextResponse.redirect(logoutUrl, { status: 307 });
  response.cookies.delete("tdp_admin_session");
  return response;
}
