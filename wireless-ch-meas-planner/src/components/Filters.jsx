/* eslint-disable react/prop-types */
import './Filters.css'
import { useId } from 'react'
import { useFilters } from '../hooks/useFilters.js'

export function Filters (){
    const {filters, setFiltersState} = useFilters()
    
    const gndSpeed = useId()
    const droneSpeed = useId()

    const handleGndSpeed = (event) =>{
        setFiltersState(previousState => (
                {...previousState, 
                    gndSpeed: event.target.value
                }
            )
        )
    }

    const handleDroneSpeed = (event) =>{
        setFiltersState(previousState => (
            {...previousState, 
                droneSpeed: event.target.value
            }
        )
    )
    }

    return (
        <section className="filters">
            <div>
                <label htmlFor={gndSpeed}>Ground speed</label>
                <input type='range'
                      step={1}
                      id={gndSpeed}
                      min='10'
                      max='50'
                      onChange={handleGndSpeed}
                      value={filters.gndSpeed}></input>
                <span>{filters.gndSpeed} km/h</span>
            </div>
            <div>
                <label htmlFor={droneSpeed}>Drone speed</label>
                <input type='range'
                      id={droneSpeed}
                      min='0.1'
                      step={0.1}
                      max='5'
                      onChange={handleDroneSpeed}
                      value={filters.droneSpeed}></input>
                <span>{filters.droneSpeed} m/s</span>
            </div>
        </section>
    )
}