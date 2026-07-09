/**
 * API 客户端
 *
 * baseURL 从环境变量读取，适配不同部署环境：
 * - 开发环境：Vite proxy 拦截 /api 请求转发到 localhost:8000
 * - 生产环境：Nginx 反代 /api 到后端
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? ''

interface RequestOptions extends RequestInit {
  params?: Record<string, string | number | undefined>
}

class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
  }

  private buildUrl(path: string, params?: Record<string, string | number | undefined>): string {
    const url = new URL(`${this.baseUrl}${path}`, window.location.origin)
    if (params) {
      for (const [key, value] of Object.entries(params)) {
        if (value !== undefined && value !== null && value !== '') {
          url.searchParams.set(key, String(value))
        }
      }
    }
    return url.pathname + url.search
  }

  async get<T>(path: string, options?: RequestOptions): Promise<T> {
    const { params, ...init } = options ?? {}
    const url = this.buildUrl(path, params)
    const resp = await fetch(url, {
      ...init,
      method: 'GET',
      headers: { 'Content-Type': 'application/json', ...init.headers },
    })
    if (!resp.ok) {
      throw new ApiError(resp.status, await resp.text())
    }
    return resp.json() as Promise<T>
  }

  async post<T>(path: string, body: unknown, options?: RequestOptions): Promise<T> {
    const { params, ...init } = options ?? {}
    const url = this.buildUrl(path, params)
    const resp = await fetch(url, {
      ...init,
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...init.headers },
      body: JSON.stringify(body),
    })
    if (!resp.ok) {
      throw new ApiError(resp.status, await resp.text())
    }
    return resp.json() as Promise<T>
  }
}

export class ApiError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(`API Error ${status}: ${message}`)
    this.name = 'ApiError'
    this.status = status
  }
}

export const apiClient = new ApiClient(BASE_URL)
