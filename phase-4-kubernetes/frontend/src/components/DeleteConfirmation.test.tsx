import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import DeleteConfirmation from './DeleteConfirmation'

describe('DeleteConfirmation', () => {
  const defaultProps = {
    isOpen: true,
    onClose: vi.fn(),
    onConfirm: vi.fn(),
    isDeleting: false,
  }

  it('renders when open', () => {
    render(<DeleteConfirmation {...defaultProps} />)
    expect(screen.getByText(/are you sure you want to delete this task/i)).toBeInTheDocument()
  })

  it('does not render when closed', () => {
    render(<DeleteConfirmation {...defaultProps} isOpen={false} />)
    expect(screen.queryByText(/are you sure you want to delete this task/i)).not.toBeInTheDocument()
  })

  it('displays warning message', () => {
    render(<DeleteConfirmation {...defaultProps} />)
    expect(screen.getByText(/this action cannot be undone/i)).toBeInTheDocument()
  })

  it('calls onClose when Cancel is clicked', async () => {
    const user = userEvent.setup()
    const onClose = vi.fn()
    render(<DeleteConfirmation {...defaultProps} onClose={onClose} />)

    const cancelButton = screen.getByRole('button', { name: /cancel/i })
    await user.click(cancelButton)

    expect(onClose).toHaveBeenCalledTimes(1)
  })

  it('calls onConfirm when Delete is clicked', async () => {
    const user = userEvent.setup()
    const onConfirm = vi.fn()
    render(<DeleteConfirmation {...defaultProps} onConfirm={onConfirm} />)

    const deleteButton = screen.getByRole('button', { name: /^delete$/i })
    await user.click(deleteButton)

    expect(onConfirm).toHaveBeenCalledTimes(1)
  })

  it('disables Cancel button when deleting', () => {
    render(<DeleteConfirmation {...defaultProps} isDeleting={true} />)
    const cancelButton = screen.getByRole('button', { name: /cancel/i })
    expect(cancelButton).toBeDisabled()
  })

  it('shows loading text when deleting', () => {
    render(<DeleteConfirmation {...defaultProps} isDeleting={true} />)
    expect(screen.getByText(/deleting.../i)).toBeInTheDocument()
  })

  it('has both Cancel and Delete buttons', () => {
    render(<DeleteConfirmation {...defaultProps} />)
    expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /^delete$/i })).toBeInTheDocument()
  })
})
