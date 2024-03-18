import {MapContainer, TileLayer} from 'react-leaflet';
import './MapToInteract.css';
import { osm_provider } from '../constants/osm-info';
import { DrawControl } from './DrawControl';

export function MapToInteract() {
 
    return (
            <div className='map-container'>
            <MapContainer 
                    center={[51.505, -0.09]}
                    zoom={15}
                    style={{height:"100%", width:"100%"}}>
                <DrawControl>
                </DrawControl>
                <TileLayer
                    attribution={osm_provider.attribution}
                    url={osm_provider.url}/>
            </MapContainer>
            </div>
        )
}