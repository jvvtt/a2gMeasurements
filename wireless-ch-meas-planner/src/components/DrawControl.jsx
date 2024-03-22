import { useMap, FeatureGroup } from "react-leaflet"
import { EditControl } from "react-leaflet-draw"
import { useContext } from 'react';
import { DroneMarkersContext } from '../context/dronemarkers.jsx';
import { GroundMarkersContext } from '../context/groundmarkers.jsx'

export function DrawControl () {
    const geo_map = useMap()   
    const {onCreationGroundMarker, onEditGroundMarker} = useContext(GroundMarkersContext)
    const {onCreationMap, onEditMove} = useContext(DroneMarkersContext);

    const handleCreated = (e) => {
        if (e.layerType == 'marker') {
            onCreationMap({layer: e.layer});
        }
        else if (e.layerType == 'circlemarker') {
            onCreationGroundMarker({layer: e.layer})
        }        
    }

    const handleEditMove = (e) => {
        onEditMove(geo_map);
    }
    
    return (
        <FeatureGroup>
            <EditControl
                        draw={{rectangle:false, 
                               polyline: false,
                               circle:false}}  
                        position='topright'
                        onCreated={(event)=>handleCreated(event)}
                        onEditMove={(e)=>handleEditMove(e)}>
            </EditControl>
        </FeatureGroup>
    )
}