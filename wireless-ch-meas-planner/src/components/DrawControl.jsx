import { useMap, FeatureGroup } from "react-leaflet"
import { EditControl } from "react-leaflet-draw"
import { useContext } from 'react';
import { MapContext } from '../context/map';

export function DrawControl () {
    const geo_map = useMap()

    const {onCreationMap, onEditMap} = useContext(MapContext);

    const handleCreated = (e) => {
        onCreationMap({layerType: e.layerType, layer: e.layer});
    }

    const handleOnEditStop = () => {
        onEditMap(geo_map);
    }

    return (
        <FeatureGroup>
            <EditControl
                        position='topright'
                        onCreated={(event)=>handleCreated(event)}
                        onEditStop={(e)=>handleOnEditStop(e)}>
            </EditControl>
        </FeatureGroup>
    )
}