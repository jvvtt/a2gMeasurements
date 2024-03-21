import { createContext, useReducer } from "react";
import { initialState, DRAW_ACTION_TYPES, reducer } from "../reducers/map.js";

export const MapContext = createContext()

function useMapReducer(){
    const [state, dispatch] = useReducer(reducer, initialState)

    const onCreationMap = map => dispatch({
        type: DRAW_ACTION_TYPES.ADD_MARKER,
        payload: map
    })

    const onEditMove = map => dispatch({
        type: DRAW_ACTION_TYPES.EDIT_MARKER,
        payload: map
    })

    return { state, onCreationMap, onEditMove}
}

// eslint-disable-next-line react/prop-types
export function MapProvider({children}){
    const {state, onCreationMap, onEditMove} = useMapReducer()
    return(
        <MapContext.Provider 
            value={{ markers: state, onCreationMap, onEditMove}}>
            {children}
        </MapContext.Provider>
    )
}