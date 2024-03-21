import {MapContainer, TileLayer} from 'react-leaflet';
import './MapToInteract.css';
import { osm_provider } from '../constants/constants.js';
import { DrawControl } from './DrawControl';
import { DrawMapObjects } from './DrawMapObjects.jsx';
import { FlightGeography } from './FlightGeography.jsx';

export function MapToInteract() {
 
    return (
            <div className='map-container'>
            <MapContainer 
                    center={[60.167120, 24.939156]}
                    zoom={13}
                    style={{height:"100%", width:"100%"}}>
                <DrawControl>
                </DrawControl>
                <TileLayer
                    attribution={osm_provider.attribution}
                    url={osm_provider.url}/>
                <DrawMapObjects></DrawMapObjects>
                <FlightGeography></FlightGeography>
            </MapContainer>
            <section className='legends-info'>
                <div className='legends-info-item'>
                    <strong>Flight Geography</strong>
                    <div className='img-info-item'>hhhh</div>
                </div>
                <div className='legends-info-item'>
                    <strong>Contingency Volume</strong>
                    <div className='img-info-item'>hhhh</div>
                </div>
                <div className='legends-info-item'>
                    <strong>Ground Risk Buffer</strong>
                    <div className='img-info-item'>hhhh</div>
                </div>
                <div className='legends-info-item'>
                    <strong>Drone location</strong>
                    <div className='img-info-item'>hhhh</div>
                </div>
                <div className='legends-info-item'>
                    <strong>Ground location</strong>
                    <div className='img-info-item'>hhhh</div>
                </div>
                <div className='legends-info-item'>
                    <strong>Drone route</strong>
                    <div className='img-info-item'>hhhh</div>
                </div>
            </section>
            </div>
        )
}