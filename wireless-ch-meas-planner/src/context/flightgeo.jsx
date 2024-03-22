import { createContext, useState } from "react"

export const FlightGeography = createContext()

// eslint-disable-next-line react/prop-types
export function FlightGeography ({children}){

    const [fgVertex, setFgVertex] = useState([])

    return (
        <FlightGeography.Provider value={{
            fgVertex,
            setFgVertex
        }}>
            {children}
        </FlightGeography.Provider>
    )
}
