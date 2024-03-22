import { handleHoverMarker, DRAW_ACTION_TYPES } from "../logic/utils.js"

export const initialState = []

const handleHoverDroneMarker = (e, n_states, id) => {
    handleHoverMarker(e, n_states, id, 'table-drone')
}

export const reducer = (state, action) => {
    const {type: actionType, payload: this_map} = action
    
    switch (actionType) {
        case DRAW_ACTION_TYPES.ADD_MARKER: {                    
            const { layer } = this_map
            const id = layer._leaflet_id
            const n_states = state.length
                    
            // Defining interactivity for when the user hovers over the marker
            layer.editing._marker.on('mouseover', (e)=> handleHoverDroneMarker(e, n_states, id)) 
                
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
            const n_states = state.length
            let idxMarkerChanged;
            /* 
               React requires that a value is provided for any created variable.

               It would be good to initialize 'newCoords' with the coords of the marker selected,
               but that is precisely what we don't know.

               If the initialized newCoords are shown, there is a strange error. 
            */
            let newCoords = {lat: state[0].lat, lng: state[0].lng}

            // FIRST: Retrieve the marker that was moved and its new coords
            for (const [, val] of Object.entries(this_map._layers)){
                if (val._latlng === undefined) {
                    continue;
                } else {
                    idxMarkerChanged = state.findIndex(entry => (val._latlng.lat !== entry.lat || 
                                                                    val._latlng.lng !== entry.lng) && 
                                                                    (val._leaflet_id === entry.id))
                    
                    if (idxMarkerChanged>= 0) {
                        newCoords = val._latlng
                        break;
                    }
                }
            }

            const newState = structuredClone(state)
            
            if (n_states > 1) {
                let dist, prevCoords, nextCoords;
                switch (idxMarkerChanged) {
                    // Error handling of ReactStrictMode
                    case -1:
                        break;
                    // Check the beginnig
                    case 0:
                        nextCoords = L.latLng(newState[idxMarkerChanged+1].lat, newState[idxMarkerChanged+1].lng)
                        dist = this_map.distance(newCoords, nextCoords)
                        newState[idxMarkerChanged+1] = {
                            ...newState[idxMarkerChanged+1],
                            distToPrevious:dist,
                        } 
                        break;
                    // Check the end
                    case n_states - 1:
                        prevCoords = L.latLng(newState[idxMarkerChanged-1].lat, newState[idxMarkerChanged-1].lng)
                        dist = this_map.distance(prevCoords, newCoords)
                        
                        newState[idxMarkerChanged] = {
                            ...newState[idxMarkerChanged],
                            distToPrevious:dist,
                        } 
                        break;
                    // Check the middle
                    default:       
                        prevCoords = L.latLng(newState[idxMarkerChanged-1].lat, newState[idxMarkerChanged-1].lng)
                        nextCoords = L.latLng(newState[idxMarkerChanged+1].lat, newState[idxMarkerChanged+1].lng)
                        dist = this_map.distance(prevCoords, newCoords)
        
                        newState[idxMarkerChanged] = {
                            ...newState[idxMarkerChanged],
                            distToPrevious:dist,
                        } 
        
                        dist = this_map.distance(newCoords, nextCoords)
                        newState[idxMarkerChanged+1] = {
                            ...newState[idxMarkerChanged+1],
                            distToPrevious:dist,
                        } 
                }
            }    

            newState[idxMarkerChanged] = {
                ...newState[idxMarkerChanged],
                lat: newCoords.lat,
                lng: newCoords.lng,
            } 

            return newState
        }         
    }
    return state
}