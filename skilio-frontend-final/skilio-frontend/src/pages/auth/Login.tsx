import { useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { clsx } from 'clsx'

import { useLogin } from '@/hooks/useAuth'
import { getApiErrorMessage } from '@/api/client'
import { Spinner } from '@/components/ui/Spinner'
import { ErrorMessage } from '@/components/ui/ErrorMessage'

interface FormValues {
  email: string
  password: string
}

export function LoginPage() {
  const location = useLocation()
  const login    = useLogin()

  const {
    register,
    handleSubmit,
    formState: { errors },
    setFocus,
  } = useForm<FormValues>()

  // Auto-focus email field on mount
  useEffect(() => { setFocus('email') }, [setFocus])

  // Did the user just register successfully?
  const justRegistered = location.state?.registered === true

  function onSubmit(values: FormValues) {
    login.mutate({ username: values.email, password: values.password })
  }

  return (
    <div className="min-h-screen bg-surface-50 flex">

      {/* ── Left panel — decorative ── */}
      <div className="hidden lg:flex lg:w-1/2 bg-surface-900 relative overflow-hidden flex-col justify-between p-12">
        {/* Geometric background pattern */}
        <div className="absolute inset-0 opacity-[0.06]">
          <div className="absolute top-20 left-10 w-64 h-64 rounded-full border-[40px] border-primary-400" />
          <div className="absolute bottom-32 right-8 w-48 h-48 rounded-full border-[30px] border-accent-400" />
          <div className="absolute top-1/2 left-1/3 w-32 h-32 rotate-45 border-[20px] border-primary-300" />
          <div className="absolute top-40 right-20 w-20 h-20 border-[12px] border-accent-300 rounded-xl" />
        </div>

        {/* Logo */}
        <div className="relative flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-primary-500 flex items-center justify-center shadow-glow-primary">
            <span className="text-white font-display font-bold text-lg">S</span>
          </div>
          <span className="font-display text-2xl font-semibold text-white tracking-tight">
            Skilio
          </span>
        </div>

        {/* Tagline */}
        <div className="relative">
          <blockquote className="font-display text-3xl font-light text-white leading-snug mb-6">
            "Every child deserves the skills to{' '}
            <em className="text-primary-300 not-italic font-semibold">stay safe</em>{' '}
            and thrive."
          </blockquote>
          <p className="text-surface-400 text-sm">
            Interactive scenario-based learning for children aged 4–17.
          </p>
        </div>
      </div>

      {/* ── Right panel — login form ── */}
      <div className="flex-1 flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-sm">

          {/* Mobile logo */}
          <div className="flex items-center gap-2 mb-10 lg:hidden">
            <div className="w-8 h-8 rounded-xl bg-primary-500 flex items-center justify-center">
              <span className="text-white font-display font-bold text-sm">S</span>
            </div>
            <span className="font-display text-xl font-semibold text-surface-900">Skilio</span>
          </div>

          {/* Header */}
          <div className="mb-8">
            <h1 className="font-display text-3xl font-semibold text-surface-900 mb-1">
              Welcome back
            </h1>
            <p className="text-surface-400 text-sm">
              Sign in to your parent account
            </p>
          </div>

          {/* Success banner after registration */}
          {justRegistered && (
            <div className="mb-5 flex items-center gap-2.5 rounded-xl border border-primary-200 bg-primary-50 px-4 py-3 text-sm text-primary-700 animate-fade-in">
              <span>✓</span>
              <span>Account created! Sign in to get started.</span>
            </div>
          )}

          {/* API error */}
          {login.isError && (
            <ErrorMessage
              message={getApiErrorMessage(login.error)}
              className="mb-5 animate-scale-in"
            />
          )}

          {/* Form */}
          <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-5">
            <div>
              <label htmlFor="email" className="label">
                Email address
              </label>
              <input
                id="email"
                type="email"
                autoComplete="email"
                placeholder="parent@example.com"
                className={clsx('input', errors.email && 'input-error')}
                {...register('email', {
                  required: 'Email is required',
                  pattern: {
                    value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                    message: 'Enter a valid email address',
                  },
                })}
              />
              {errors.email && (
                <p className="field-error">{errors.email.message}</p>
              )}
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label htmlFor="password" className="label mb-0">
                  Password
                </label>
              </div>
              <input
                id="password"
                type="password"
                autoComplete="current-password"
                placeholder="••••••••"
                className={clsx('input', errors.password && 'input-error')}
                {...register('password', {
                  required: 'Password is required',
                  minLength: { value: 8, message: 'Password must be at least 8 characters' },
                })}
              />
              {errors.password && (
                <p className="field-error">{errors.password.message}</p>
              )}
            </div>

            <button
              type="submit"
              disabled={login.isPending}
              className="btn-primary btn-lg w-full mt-2"
            >
              {login.isPending ? (
                <>
                  <Spinner size="sm" className="border-white/30 border-t-white" />
                  Signing in…
                </>
              ) : (
                'Sign in'
              )}
            </button>
          </form>

          {/* Register link */}
          <p className="mt-6 text-center text-sm text-surface-400">
            Don't have an account?{' '}
            <Link
              to="/register"
              className="font-semibold text-primary-600 hover:text-primary-700 transition-colors"
            >
              Create one free
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
