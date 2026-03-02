import { Check } from 'lucide-react'

interface Step {
  id: string
  label: string
  completed: boolean
  current: boolean
}

interface ProjectProgressProps {
  steps: Step[]
  onStepClick?: (stepId: string) => void
}

export default function ProjectProgress({ steps, onStepClick }: ProjectProgressProps) {
  return (
    <div className="card">
      <div className="flex items-center justify-between">
        {steps.map((step, index) => (
          <div key={step.id} className="flex items-center flex-1">
            {/* Step Circle */}
            <div className="flex flex-col items-center">
              <button
                onClick={() => onStepClick?.(step.id)}
                disabled={!onStepClick}
                className={`flex items-center justify-center w-10 h-10 rounded-full border-2 transition-all ${
                  step.completed
                    ? 'bg-green-500 border-green-500 text-white hover:bg-green-600'
                    : step.current
                    ? 'bg-primary-500 border-primary-500 text-white hover:bg-primary-600'
                    : 'bg-white border-gray-300 text-gray-400 hover:border-gray-400'
                } ${onStepClick ? 'cursor-pointer' : 'cursor-default'}`}
              >
                {step.completed ? (
                  <Check className="h-5 w-5" />
                ) : (
                  <span className="text-sm font-semibold">{index + 1}</span>
                )}
              </button>
              <button
                onClick={() => onStepClick?.(step.id)}
                disabled={!onStepClick}
                className={`mt-2 text-xs font-medium ${
                  step.completed
                    ? 'text-green-600 hover:text-green-700'
                    : step.current
                    ? 'text-primary-600 hover:text-primary-700'
                    : 'text-gray-400 hover:text-gray-500'
                } ${onStepClick ? 'cursor-pointer' : 'cursor-default'}`}
              >
                {step.label}
              </button>
            </div>

            {/* Connector Line */}
            {index < steps.length - 1 && (
              <div
                className={`flex-1 h-0.5 mx-2 transition-all ${
                  step.completed ? 'bg-green-500' : 'bg-gray-300'
                }`}
              />
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
