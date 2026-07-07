import { renderHook, act } from '@testing-library/react'
import { useAppStore } from '../src/store/useAppStore'

test('setActiveDataset updates store and sets first tab as active', () => {
  const { result } = renderHook(() => useAppStore())
  const dataset = { id: '1', name: 'Test', tabNames: ['Sheet1', 'Sheet2'], tabs: [], createdAt: '' }
  act(() => result.current.setActiveDataset(dataset))
  expect(result.current.activeDataset?.id).toBe('1')
  expect(result.current.activeTab).toBe('Sheet1')
})

test('clearChat empties chat messages', () => {
  const { result } = renderHook(() => useAppStore())
  act(() => result.current.addChatMessage({ id: '1', role: 'user', content: 'hi', timestamp: '' }))
  act(() => result.current.clearChat())
  expect(result.current.chatMessages).toHaveLength(0)
})
