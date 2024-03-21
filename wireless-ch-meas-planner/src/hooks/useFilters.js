import { FiltersContext } from '../context/filters.jsx'
import { useContext } from 'react'

export function useFilters () {
    const {filters, setFiltersState} = useContext(FiltersContext)
  
    const timeToPrevious = (points, node) => {
        return points.map(point => {
            return node === 'DRONE' ? point.distToPrevious/filters.droneSpeed : point.distToPrevious/filters.gndSpeed
        })
    }
    return {setFiltersState, timeToPrevious, filters}
  }