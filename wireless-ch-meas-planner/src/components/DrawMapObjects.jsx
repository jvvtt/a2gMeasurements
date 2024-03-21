import { Polyline } from "react-leaflet";
import { MapContext } from "../context/map";
import { useContext } from "react";

export function DrawMapObjects () {

    const {markers} = useContext(MapContext)

    return (
        <>
            { markers.map((entry, cnt)=> {
                if (cnt > 0) {
                    const position = [[entry.lat, entry.lng], [markers[cnt-1].lat, markers[cnt-1].lng]];
                    return(
                        <Polyline key={cnt} pathOptions={{color: 'lime'}} positions={position}></Polyline>
                    )
                }                
            })}        
        </>
    )
}