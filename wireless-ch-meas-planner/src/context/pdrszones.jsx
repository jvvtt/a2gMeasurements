import { createContext, useState } from "react"

export const PDRSZonesContext = createContext()

// eslint-disable-next-line react/prop-types
export function PDRSZonesProvider ({children}){

    const [fgVertex, setFgVertex] = useState([])
    const [cvVertex, setCvVertex] = useState([])
    const [grbVertex, setGrbVertex] = useState([])

    return (
        <PDRSZonesContext.Provider value={{
            fgVertex,
            setFgVertex,
            cvVertex,
            setCvVertex,
            grbVertex,
            setGrbVertex
        }}>
            {children}
        </PDRSZonesContext.Provider>
    )
}
