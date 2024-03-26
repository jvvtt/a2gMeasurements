import {MapContainer, TileLayer} from 'react-leaflet';
import './MapToInteract.css';
import { osm_provider } from '../constants/constants.js';
import { DrawControl } from './DrawControl';
import { DrawDronePath, DrawDroneGimbalYaw } from './DrawMapObjs.jsx';
import { FlightGeography2 } from './PDRSZones.jsx';
import { MapLegends } from './MapLegends.jsx';

export function MapToInteract() {
 
    return (
            <div className='map-container'>
            <MapContainer 
                    center={[60.167120, 24.939156]}
                    zoom={13}
                    style={{height:"100%", width:"100%"}}>
                <DrawControl></DrawControl>
                <TileLayer
                    attribution={osm_provider.attribution}
                    url={osm_provider.url}/>
                <DrawDronePath></DrawDronePath>
                <DrawDroneGimbalYaw></DrawDroneGimbalYaw>
                <FlightGeography2></FlightGeography2>
            </MapContainer>
            <MapLegends></MapLegends>
            </div>
        )
}