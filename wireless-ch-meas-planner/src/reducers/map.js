export const DRAW_ACTION_TYPES  = {
    ADD_MARKER: 'ADD_MARKER',
    EDIT_MARKER: 'EDIT_MARKER',
}

export const initialState = []
export const reducer = (state, action) => {
    const {type: actionType, payload: actionPayload} = action
    
    switch (actionType) {
        case DRAW_ACTION_TYPES.ADD_MARKER: { 
            const { layerType, layer } = actionPayload
            
            if (layerType === 'marker') {
                layer.editing._marker.on('mouseover', () =>{console.log('marker clicked')})
                layer.editing._marker.bindTooltip('First one')
                const newState = [
                    ...state,
                    {
                        lat: layer._latlng.lat,
                        lng: layer._latlng.lng,
                        id: layer._leaflet_id,
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

            actionPayload.eachLayer(layer=>{
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