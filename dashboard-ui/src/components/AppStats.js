import React, { useEffect, useState } from 'react'
import '../App.css';

export default function AppStats() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null)

	const getStats = () => {
	
        fetch(`http://kafka.westus.cloudapp.azure.com:8100/events/stats`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received Stats")
                setStats(result);
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    }
    useEffect(() => {
		const interval = setInterval(() => getStats(), 2000); // Update every 2 seconds
		return() => clearInterval(interval);
    }, [getStats]);

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        return(
            <div>
                <h1>Latest Stats</h1>
                <table className={"stats"}>
					<tbody>
						<tr>
							<th>Xp Gained</th>
							<th>Item Pickup</th>
						</tr>
						<tr>
							<td># XP: {stats['item_total']}</td>
							<td># ITEM: {stats['xp_total']}</td>
						</tr>
						<tr>
							<td colspan="2">Max Item Gained: {stats['item_max_gain']}</td>
						</tr>
						<tr>
							<td colspan="2">Max XP Gained: {stats['xp_max_gain']}</td>
						</tr>
					</tbody>
                </table>
                <h3>Last Updated: {stats['last_updated']}</h3>

            </div>
        )
    }
}
