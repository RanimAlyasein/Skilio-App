import { useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { clsx } from 'clsx'

import { useRegister } from '@/hooks/useAuth'
import { getApiErrorMessage } from '@/api/client'
import { Spinner } from '@/components/ui/Spinner'
import { ErrorMessage } from '@/components/ui/ErrorMessage'

interface FormValues {
  full_name: string
  email: string
  password: string
  confirm_password: string
}

export function RegisterPage() {
  const registerMutation = useRegister()

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
    setFocus,
  } = useForm<FormValues>()

  useEffect(() => { setFocus('full_name') }, [setFocus])

  const passwordValue = watch('password', '')

  function onSubmit(values: FormValues) {
    registerMutation.mutate({
      email:     values.email,
      full_name: values.full_name,
      password:  values.password,
    })
  }

  return (
    <div className="min-h-screen bg-surface-50 flex">

      {/* ── Left decorative panel ── */}
      <div className="hidden lg:flex lg:w-1/2 bg-surface-900 relative overflow-hidden flex-col justify-between p-12">
        <div className="absolute inset-0 opacity-[0.06]">
          <div className="absolute top-16 right-12 w-72 h-72 rounded-full border-[40px] border-accent-400" />
          <div className="absolute bottom-20 left-10 w-52 h-52 rounded-full border-[32px] border-primary-400" />
          <div className="absolute top-1/2 right-1/4 w-28 h-28 rotate-12 border-[16px] border-primary-300 rounded-2xl" />
        </div>

        <div className="relative flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-primary-500 flex items-center justify-center">
            <span className="text-white font-display font-bold text-lg">S</span>
          </div>
          <span className="font-display text-2xl font-semibold text-white">Skilio</span>
        </div>

        <div className="relative space-y-4">
          {[
            { icon: '◈', text: 'Branching story scenarios your child actually engages with' },
            { icon: '⭐', text: 'XP, badges, and progress dashboards for real motivation' },
            { icon: '◎', text: "Full visibility into every choice your child makes" },
          ].map((item) => (
            <div key={item.icon} className="flex items-start gap-3">
              <span className="text-primary-300 text-lg mt-0.5 shrink-0">{item.icon}</span>
              <p className="text-surface-300 text-sm leading-relaxed">{item.text}</p>
            </div>
          ))}
        </div>
      </div>

      {/* ── Right — registration form ── */}
      <div className="flex-1 flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-sm">

          <div className="flex items-center gap-2 mb-10 lg:hidden">
            <div className="w-8 h-8 rounded-xl bg-primary-500 flex items-center justify-center">
              <span className="text-white font-display font-bold text-sm">S</span>
            </div>
            <span className="font-display text-xl font-semibold text-surface-900">Skilio</span>
          </div>

          <div className="mb-8">
            <h1 className="font-display text-3xl font-semibold text-surface-900 mb-1">
              Create your account
            </h1>
            <p className="text-surface-400 text-sm">
              Set up your parent account in under a minute
            </p>
          </div>

          {registerMutation.isError && (
            <ErrorMessage
              message={getApiErrorMessage(registerMutation.error)}
              className="mb-5 animate-scale-in"
            />
          )}

          <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-4">

            {/* Full name */}
            <div>
              <label htmlFor="full_name" className="label">Full name</label>
              <input
                id="full_name"
                type="text"
                autoComplete="name"
                placeholder="Your name"
                className={clsx('input', errors.full_name && 'input-error')}
                {...register('full_name', {
                  required: 'Full name is required',
                  minLength: { value: 2, message: 'Name must be at least 2 characters' },
                })}
              />
              {errors.full_name && (
                <p className="field-error">{errors.full_name.message}</p>
              )}
            </div>

            {/* Email */}
            <div>
              <label htmlFor="email" className="label">Email address</label>
              <input
                id="email"
                type="email"
                autoComplete="email"
                placeholder="you@example.com"
                className={clsx('input', errors.email && 'input-error')}
                {...register('email', {
                  required: 'Email is required',
                  pattern: {
                    value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                    message: 'Enter a valid email',
                  },
                })}
              />
              {errors.email && (
                <p className="field-error">{errors.email.message}</p>
              )}
            </div>

            {/* Password */}
            <div>
              <label htmlFor="password" className="label">Password</label>
              <input
                id="password"
                type="password"
                autoComplete="new-password"
                placeholder="At least 8 characters"
                className={clsx('input', errors.password && 'input-error')}
                {...register('password', {
                  required: 'Password is required',
                  minLength: { value: 8, message: 'Must be at least 8 characters' },
                  validate: {
                    hasLetter: (v) =>
                      /[a-zA-Z]/.test(v) || 'Must contain at least one letter',
                    hasNumber: (v) =>
                      /[0-9]/.test(v) || 'Must contain at least one number',
                  },
                })}
              />
              {errors.password && (
                <p className="field-error">{errors.password.message}</p>
              )}
            </div>

            {/* Confirm password */}
            <div>
              <label htmlFor="confirm_password" className="label">Confirm password</label>
              <input
                id="confirm_password"
                type="password"
                autoComplete="new-password"
                placeholder="Repeat your password"
                className={clsx('input', errors.confirm_password && 'input-error')}
                {...register('confirm_password', {
                  required: 'Please confirm your password',
                  validate: (v) =>
                    v === passwordValue || 'Passwords do not match',
                })}
              />
              {errors.confirm_password && (
                <p className="field-error">{errors.confirm_password.message}</p>
              )}
            </div>

            {/* Password strength hints */}
            {passwordValue.length > 0 && (
              <div className="flex gap-2 pt-1">
                <StrengthPill
                  label="8+ chars"
                  met={passwordValue.length >= 8}
                />
                <StrengthPill
                  label="Letter"
                  met={/[a-zA-Z]/.test(passwordValue)}
                />
                <StrengthPill
                  label="Number"
                  met={/[0-9]/.test(passwordValue)}
                />
              </div>
            )}

            <button
              type="submit"
              disabled={registerMutation.isPending}
              className="btn-primary btn-lg w-full mt-2"
            >
              {registerMutation.isPending ? (
                <>
                  <Spinner size="sm" className="border-white/30 border-t-white" />
                  Creating account…
                </>
              ) : (
                'Create account'
              )}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-surface-400">
            Already have an account?{' '}
            <Link
              to="/login"
              className="font-semibold text-primary-600 hover:text-primary-700 transition-colors"
            >
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}

// ── Password strength indicator pill ──────────────────────────────────────────
function StrengthPill({ label, met }: { label: string; met: boolean }) {
  return (
    <span
      className={clsx(
        'text-xs font-semibold px-2.5 py-1 rounded-full transition-all duration-200',
        met
          ? 'bg-primary-100 text-primary-700'
          : 'bg-surface-200 text-surface-400',
      )}
    >
      {met ? '✓ ' : ''}{label}
    </span>
  )
}
