import GeometryUtil from "leaflet-geometryutil"

export const DRAW_ACTION_TYPES  = {
    ADD_MARKER: 'ADD_MARKER',
    EDIT_MARKER: 'EDIT_MARKER',
}

const handleHoverMarker = (e, n_states, id) => {
    // Show a tooltip with the order at which the marker was created
    e.target.editing._marker.bindTooltip(`Placed as: ${n_states+1}`)

    const marker = document.getElementsByClassName("marker-values")
    
    // Show which shown coordinates correspond to the marker
    for ( const [key, liHtml] of Object.entries(marker) ) {
        let id_text =  liHtml.children[0].innerText
        if ( id_text === `${id}`) {
            liHtml.style.backgroundColor = "red"
        } else {
            liHtml.style.backgroundColor = ""
        }
    }
}

export const initialState = []
export const reducer = (state, action) => {
    const {type: actionType, payload: this_map} = action
    
    switch (actionType) {
        case DRAW_ACTION_TYPES.ADD_MARKER: { 
            const { layerType, layer } = this_map
            
            if (layerType === 'marker') {

                // Defining interactivity for when the user hovers over the marker
                const n_states = state.length
                const id = layer._leaflet_id
                layer.editing._marker.on('mouseover', (e)=> handleHoverMarker(e, n_states, id)) 
                
                let dist_this_marker_and_previous = 0
                if (n_states > 0) {
                    const coords = state[state.length-1]
                    dist_this_marker_and_previous = layer._map.distance(L.latLng(coords.lat, coords.lng), layer._latlng)
                    console.log(dist_this_marker_and_previous)
                } 
                
                console.log(L.GeometryUtil.destination(layer._latlng, 120, 50))

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
            
            else if (layerType === 'polyline') {
                1
            }

            else if (layerType === 'polygon') {
                1
            }

            else if (layerType === 'rectangle') {
                1
            }

            else if (layerType === 'circle') {
                1
            }

            else if (layerType === 'circlemarker') {
                1
            }

            return state            
        }

        case DRAW_ACTION_TYPES.EDIT_MARKER: {
            const newState = structuredClone(state)

            this_map.eachLayer(layer=>{
                if (layer._latlng !== undefined){
                    const thisMarkerIdx = state.findIndex(marker=>marker.id === layer._leaflet_id)
                    
                    newState[thisMarkerIdx] = {
                        ...newState[thisMarkerIdx],
                        lat: layer._latlng.lat,
                        lng: layer._latlng.lng,
                    } 
                }
            })
            return newState
        }         
    }
    return state
}