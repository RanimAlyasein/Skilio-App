import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { clsx } from 'clsx'

import {
  useChildren, useCreateChild, useDeleteChild, useUpdateChild,
} from '@/hooks/useChildren'
import { Avatar }       from '@/components/ui/Avatar'
import { XPBar }        from '@/components/ui/XPBar'
import { Spinner }      from '@/components/ui/Spinner'
import { EmptyState }   from '@/components/ui/EmptyState'
import { ErrorMessage } from '@/components/ui/ErrorMessage'
import { getApiErrorMessage } from '@/api/client'
import type { ChildSummary, ChildCreate } from '@/types'

export function ManageChildrenPage() {
  const { data: children, isLoading, error } = useChildren()
  const [showForm, setShowForm] = useState(false)
  const [deletingId, setDeletingId] = useState<number | null>(null)

  return (
    <div className="page-container">
      <div className="flex items-end justify-between mb-8 animate-fade-up">
        <div>
          <h1 className="page-title">My children</h1>
          <p className="page-subtitle">Create and manage your children's profiles</p>
        </div>
        <button
          onClick={() => setShowForm((v) => !v)}
          className={showForm ? 'btn-outline' : 'btn-primary'}
        >
          {showForm ? 'Cancel' : '+ Add child'}
        </button>
      </div>

      {/* ── Add child form ── */}
      {showForm && (
        <AddChildForm
          onSuccess={() => setShowForm(false)}
          className="mb-8 animate-scale-in"
        />
      )}

      {isLoading && (
        <div className="flex justify-center py-16"><Spinner size="lg" /></div>
      )}

      {error && <ErrorMessage message={getApiErrorMessage(error)} className="mb-6" />}

      {!isLoading && !error && children?.length === 0 && !showForm && (
        <EmptyState
          icon="👶"
          title="No children yet"
          description="Add your first child profile to get started."
          action={
            <button onClick={() => setShowForm(true)} className="btn-primary">
              Add first child
            </button>
          }
        />
      )}

      {children && children.length > 0 && (
        <div className="space-y-3">
          {children.map((child) => (
            <ChildRow
              key={child.id}
              child={child}
              isDeleting={deletingId === child.id}
              onDeleteStart={() => setDeletingId(child.id)}
              onDeleteEnd={() => setDeletingId(null)}
            />
          ))}
        </div>
      )}
    </div>
  )
}

// ── Add child form ─────────────────────────────────────────────────────────────

function AddChildForm({
  onSuccess,
  className,
}: {
  onSuccess: () => void
  className?: string
}) {
  const createChild = useCreateChild()
  const { register, handleSubmit, reset, formState: { errors } } = useForm<ChildCreate>()

  function onSubmit(data: ChildCreate) {
    createChild.mutate(
      { ...data, age: Number(data.age) },
      { onSuccess: () => { reset(); onSuccess() } },
    )
  }

  return (
    <div className={clsx('card p-6', className)}>
      <h2 className="font-display text-lg font-semibold text-surface-800 mb-5">
        New child profile
      </h2>

      {createChild.isError && (
        <ErrorMessage
          message={getApiErrorMessage(createChild.error)}
          className="mb-4"
        />
      )}

      <form onSubmit={handleSubmit(onSubmit)} noValidate>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-5">
          <div className="sm:col-span-2">
            <label className="label">Display name</label>
            <input
              type="text"
              placeholder="e.g. Elif"
              className={clsx('input', errors.display_name && 'input-error')}
              {...register('display_name', {
                required: 'Name is required',
                minLength: { value: 1, message: 'Name cannot be blank' },
                maxLength: { value: 50, message: 'Max 50 characters' },
              })}
            />
            {errors.display_name && (
              <p className="field-error">{errors.display_name.message}</p>
            )}
          </div>

          <div>
            <label className="label">Age</label>
            <input
              type="number"
              min={4}
              max={17}
              placeholder="8"
              className={clsx('input', errors.age && 'input-error')}
              {...register('age', {
                required: 'Age is required',
                min: { value: 4, message: 'Minimum age is 4' },
                max: { value: 17, message: 'Maximum age is 17' },
              })}
            />
            {errors.age && (
              <p className="field-error">{errors.age.message}</p>
            )}
          </div>
        </div>

        <div className="flex justify-end gap-3">
          <button
            type="submit"
            disabled={createChild.isPending}
            className="btn-primary"
          >
            {createChild.isPending ? (
              <><Spinner size="sm" className="border-white/30 border-t-white" /> Creating…</>
            ) : (
              'Create profile'
            )}
          </button>
        </div>
      </form>
    </div>
  )
}

// ── Child row ──────────────────────────────────────────────────────────────────

function ChildRow({
  child,
  isDeleting,
  onDeleteStart,
  onDeleteEnd,
}: {
  child: ChildSummary
  isDeleting: boolean
  onDeleteStart: () => void
  onDeleteEnd: () => void
}) {
  const deleteChild  = useDeleteChild()
  const [confirmDelete, setConfirmDelete] = useState(false)

  function handleDelete() {
    if (!confirmDelete) { setConfirmDelete(true); return }
    onDeleteStart()
    deleteChild.mutate(child.id, {
      onSettled: () => { setConfirmDelete(false); onDeleteEnd() },
    })
  }

  return (
    <div className="card p-5 flex items-center gap-5 animate-fade-in">
      <Avatar name={child.display_name} imageUrl={child.avatar_url} size="md" />

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="font-semibold text-surface-900">{child.display_name}</span>
          <span className="badge-gray">Age {child.age}</span>
        </div>
        <XPBar current={child.total_xp} showLabel={false} className="max-w-xs" />
        <p className="text-xs text-surface-400 mt-1">{child.total_xp} XP earned</p>
      </div>

      <div className="flex items-center gap-2 shrink-0">
        {confirmDelete ? (
          <>
            <span className="text-xs text-red-500 font-medium">Are you sure?</span>
            <button
              onClick={handleDelete}
              disabled={isDeleting}
              className="btn-danger btn-sm"
            >
              {isDeleting ? <Spinner size="sm" className="border-white/30 border-t-white" /> : 'Delete'}
            </button>
            <button
              onClick={() => setConfirmDelete(false)}
              className="btn-outline btn-sm"
            >
              Cancel
            </button>
          </>
        ) : (
          <button
            onClick={() => setConfirmDelete(true)}
            className="btn-ghost btn-sm text-surface-400 hover:text-red-500"
          >
            Remove
          </button>
        )}
      </div>
    </div>
  )
}
