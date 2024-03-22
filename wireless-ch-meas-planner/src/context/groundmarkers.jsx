import { createContext, useReducer } from "react";
import { reducer, initialState } from "../reducers/groundmarkers.js";
import { DRAW_ACTION_TYPES } from "../logic/utils.js"

export const GroundMarkersContext = createContext()

function useGroundMarkerReducer() {
    const [state, dispatch] = useReducer(reducer, initialState)

    const onCreationGroundMarker = map => dispatch({
        type: DRAW_ACTION_TYPES.ADD_MARKER,
        payload: map
    })

    const onEditGroundMarker = map => dispatch({
        type: DRAW_ACTION_TYPES.EDIT_MARKER,
        payload: map
    })

    return {state, onCreationGroundMarker, onEditGroundMarker}
}

export function GroundMarkersProvider ({children}) {
    const {state, onCreationGroundMarker, onEditGroundMarker} = useGroundMarkerReducer()
    return(
        <GroundMarkersContext.Provider value={{gndmarkers:state, onCreationGroundMarker, onEditGroundMarker}}>
            {children}
        </GroundMarkersContext.Provider>
    )
}