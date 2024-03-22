import { FiltersContext } from '../context/filters.jsx'
import { useContext } from 'react'

export function useFilters () {
    const {filters, setFiltersState} = useContext(FiltersContext)
  
    const timeToPrevious = (points, node) => {
        const kmh2ms = (1000/3600)
        return points.map(point => {
            return node === 'DRONE' ? point.distToPrevious/filters.droneSpeed : point.distToPrevious/(filters.gndSpeed*kmh2ms)
        })
    }
    return {setFiltersState, timeToPrevious, filters}
  }