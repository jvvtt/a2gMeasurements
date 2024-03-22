import { DRAW_ACTION_TYPES, handleHoverMarker } from "../logic/utils"

// Add a Tooltip to the circle marker
const handleHoverCircleMarker = (e, n_states, id) =>{
    handleHoverMarker(e, n_states, id, 'table-ground')
}

export const initialState = []

export function reducer (state, action) {

    const {type: actionType, payload: this_map} = action

    switch(actionType) {
        case DRAW_ACTION_TYPES.ADD_MARKER: {
            const { layer } = this_map
            const id = layer._leaflet_id
            const n_states = state.length
                    
            // Defining interactivity for when the user hovers over the marker
            layer.editing._shape.on('mouseover', (e)=> handleHoverCircleMarker(e, n_states, id)) 
                
            let dist_this_marker_and_previous = 0
            if (n_states > 0) {
                const coords = state[state.length-1]
                dist_this_marker_and_previous = layer._map.distance(L.latLng(coords.lat, coords.lng), layer._latlng)
            } 
                
            const newState = [
                ...state,
                {
                    lat: layer._latlng.lat,
                    lng: layer._latlng.lng,
                    id: id,
                    distToPrevious: dist_this_marker_and_previous,
                }
            ]
            return newState
        }            
        case DRAW_ACTION_TYPES.EDIT_MARKER: {

            return state
        }        
    }
    return state
}