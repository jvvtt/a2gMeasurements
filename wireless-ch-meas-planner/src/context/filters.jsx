import { createContext, useState } from "react"

export const FiltersContext = createContext()

// eslint-disable-next-line react/prop-types
export function FiltersProvider ({children}){
    const [filters, setFiltersState] = useState(
        {
            droneSpeed: 0.1,
            gndSpeed: 10,
        }
    )

    return (
        <FiltersContext.Provider value={{
            filters,
            setFiltersState
        }}>
            {children}
        </FiltersContext.Provider>
    )
}
