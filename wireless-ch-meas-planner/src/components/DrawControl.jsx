import { useMap, FeatureGroup } from "react-leaflet"
import { EditControl } from "react-leaflet-draw"
import { useContext } from 'react';
import { MapContext } from '../context/map';

export function DrawControl () {
    const geo_map = useMap()   

    const {onCreationMap, onEditMove} = useContext(MapContext);

    const handleCreated = (e) => {
        onCreationMap({layerType: e.layerType, layer: e.layer});
    }

    const handleEditMove = () => {
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