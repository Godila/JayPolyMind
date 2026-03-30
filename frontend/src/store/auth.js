/**
 * Minimal auth store — localStorage-backed, no Pinia required.
 * Stores: token + { username, role }
 */

const TOKEN_KEY = 'jpm_auth_token'
const USER_KEY  = 'jpm_auth_user'   // JSON: { username, role }

export const isAuthenticated = () => !!localStorage.getItem(TOKEN_KEY)

export const getToken = () => localStorage.getItem(TOKEN_KEY)

export const getUser = () => {
  try {
    return JSON.parse(localStorage.getItem(USER_KEY) || 'null')
  } catch {
    return null
  }
}

export const login = (token, username, role) => {
  localStorage.setItem(TOKEN_KEY, token)
  localStorage.setItem(USER_KEY, JSON.stringify({ username, role }))
}

export const logout = () => {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}
