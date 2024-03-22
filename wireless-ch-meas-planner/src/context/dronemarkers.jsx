import { createContext, useReducer } from "react";
import { initialState, reducer } from "../reducers/dronemarkers.js";
import { DRAW_ACTION_TYPES } from "../logic/utils.js"

export const DroneMarkersContext = createContext()

function useMapReducer(){
    const [state, dispatch] = useReducer(reducer, initialState)

    const onCreationMap = layer => dispatch({
        type: DRAW_ACTION_TYPES.ADD_MARKER,
        payload: layer
    })

    const onEditMove = map => dispatch({
        type: DRAW_ACTION_TYPES.EDIT_MARKER,
        payload: map
    })

    return { state, onCreationMap, onEditMove}
}

// eslint-disable-next-line react/prop-types
export function DroneMarkersProvider({children}){
    const {state, onCreationMap, onEditMove} = useMapReducer()
    return(
        <DroneMarkersContext.Provider 
            value={{ markers: state, onCreationMap, onEditMove}}>
            {children}
        </DroneMarkersContext.Provider>
    )
}