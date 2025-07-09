import { useState, useEffect } from "react";
import { usePartyState } from "@/hooks/usePartyState";
import { TokenResult } from "@/app/api/token/route";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { CheckedState } from "@radix-ui/react-checkbox";

interface LobbyProps {
  partyId: string;
}

export default function Lobby({ partyId }: LobbyProps) {
  const [name, setName] = useState<string>("");
  const [isHost, setIsHost] = useState<boolean>(false);
  const [isAutoJoining, setIsAutoJoining] = useState<boolean>(false);
  const { dispatch } = usePartyState();

  // Read URL parameters and auto-join if specified
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const nameParam = urlParams.get('name');
    const hostParam = urlParams.get('host');
    const autoJoinParam = urlParams.get('autoJoin');

    console.log("🔍 URL Parameters:", { nameParam, hostParam, autoJoinParam });

    // Pre-populate form with URL parameters
    if (nameParam) {
      setName(nameParam);
    }
    if (hostParam === 'true') {
      setIsHost(true);
    }

    // Auto-join if specified and we have a name
    if (autoJoinParam === 'true' && nameParam) {
      setIsAutoJoining(true);
      console.log("🎯 Auto-join requested, waiting for component to be ready...");
      
      // Add delay to ensure LiveKit context is fully initialized
      const autoJoinTimer = setTimeout(() => {
        console.log("🚀 Starting delayed auto-join...");
        handleJoinWithParams(nameParam, hostParam === 'true');
      }, 2000); // 2 second delay to ensure LiveKit room component is fully ready

      // Cleanup timer if component unmounts
      return () => clearTimeout(autoJoinTimer);
    }
  }, []);

  const handleJoinWithParams = async (userName: string, isHostUser: boolean, retryCount = 0) => {
    try {
      console.log("🎫 Auto-joining with params:", { userName, isHostUser, attempt: retryCount + 1 });
      
      // Validate parameters
      if (!userName || userName.trim() === '') {
        throw new Error("❌ Username is empty or invalid");
      }
      
      // Debug: Check environment variables
      console.log("🔍 Environment Check:");
      console.log("NEXT_PUBLIC_LIVEKIT_URL:", process.env.NEXT_PUBLIC_LIVEKIT_URL);

      if (!process.env.NEXT_PUBLIC_LIVEKIT_URL) {
        throw new Error("❌ NEXT_PUBLIC_LIVEKIT_URL is not set in .env.local");
      }

      // Fetch the token from the /api/token endpoint
      console.log("🎫 Fetching token...");
      const response = await fetch(
        `/api/token?party_id=${encodeURIComponent(
          partyId
        )}&name=${encodeURIComponent(userName.trim())}&host=${isHostUser}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        const errorText = await response.text();
        console.error("❌ Token fetch failed:", response.status, errorText);
        
        // Retry logic for auto-join
        if (retryCount < 2) {
          console.log(`🔄 Retrying auto-join in 2 seconds... (attempt ${retryCount + 2}/3)`);
          setTimeout(() => {
            handleJoinWithParams(userName, isHostUser, retryCount + 1);
          }, 2000);
          return;
        }
        
        throw new Error(`Failed to fetch token: ${response.status} - ${errorText}`);
      }

      const data = (await response.json()) as TokenResult;
      console.log("✅ Token received:");
      console.log("Server URL:", data.serverUrl);
      console.log("Identity:", data.identity);

      // Dispatch actions with small delays to ensure proper state management
      console.log("📤 Dispatching token and server URL...");
      dispatch({ type: "SET_TOKEN", payload: data.token });
      dispatch({ type: "SET_SERVER_URL", payload: data.serverUrl });
      dispatch({ type: "SET_IS_HOST", payload: isHostUser });
      
      // Add a small delay before triggering connection to ensure all state is set
      setTimeout(() => {
        console.log("📤 Dispatching connection trigger...");
        dispatch({ type: "SET_SHOULD_CONNECT", payload: true });
        console.log("🚀 Successfully triggered LiveKit connection for auto-join!");
      }, 100);
    } catch (error) {
      console.error("❌ Auto-join Error:", error);
      const errorMessage = error instanceof Error ? error.message : String(error);
      
      // Only show alert if this is the final retry
      if (retryCount >= 2) {
        alert(`Auto-join failed: ${errorMessage}\n\nPlease try joining manually.`);
      }
      
      setIsAutoJoining(false);
    }
  };

  const handleJoin = async () => {
    try {
      console.log("🎫 Manual join with params:", { name, isHost });
      
      // Validate parameters
      if (!name || name.trim() === '') {
        throw new Error("❌ Please enter your name");
      }
      
      // Debug: Check environment variables
      console.log("🔍 Environment Check:");
      console.log("NEXT_PUBLIC_LIVEKIT_URL:", process.env.NEXT_PUBLIC_LIVEKIT_URL);
      console.log("Has LIVEKIT_API_KEY:", !!process.env.LIVEKIT_API_KEY);
      console.log("Has LIVEKIT_API_SECRET:", !!process.env.LIVEKIT_API_SECRET);

      if (!process.env.NEXT_PUBLIC_LIVEKIT_URL) {
        throw new Error("❌ NEXT_PUBLIC_LIVEKIT_URL is not set in .env.local");
      }

      // Fetch the token from the /api/token endpoint
      console.log("🎫 Fetching token...");
      const response = await fetch(
        `/api/token?party_id=${encodeURIComponent(
          partyId
        )}&name=${encodeURIComponent(name.trim())}&host=${isHost}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        const errorText = await response.text();
        console.error("❌ Token fetch failed:", response.status, errorText);
        throw new Error(`Failed to fetch token: ${response.status} - ${errorText}`);
      }

      const data = (await response.json()) as TokenResult;
      console.log("✅ Token received:");
      console.log("Server URL:", data.serverUrl);
      console.log("Identity:", data.identity);

      // Dispatch actions with consistent timing
      console.log("📤 Dispatching token and server URL for manual join...");
      dispatch({ type: "SET_TOKEN", payload: data.token });
      dispatch({ type: "SET_SERVER_URL", payload: data.serverUrl });
      dispatch({ type: "SET_IS_HOST", payload: isHost });
      
      // Add a small delay before triggering connection
      setTimeout(() => {
        console.log("📤 Dispatching connection trigger for manual join...");
        dispatch({ type: "SET_SHOULD_CONNECT", payload: true });
        console.log("🚀 Successfully triggered LiveKit connection for manual join!");
      }, 100);
    } catch (error) {
      console.error("❌ Manual Join Error:", error);
      const errorMessage = error instanceof Error ? error.message : String(error);
      alert(`Connection Error: ${errorMessage}\n\nCheck console for details.`);
    }
  };

  const onJoin = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault(); // Prevent the default form submission behavior
    await handleJoin();
  };

  return (
    <div className="w-full h-full flex items-center justify-center bg-transparent">
      <Card className="bg-transparent border-transparent shadow-none">
        <form action="#" onSubmit={onJoin}>
          <CardHeader>
            <CardTitle>Join Party</CardTitle>
            <CardDescription>
              {isAutoJoining ? "Auto-joining party..." : "Join or create a party to chat or listen in"}
            </CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col space-y-4">
            <div className="flex flex-col space-y-1.5">
              <Label htmlFor="name">Name</Label>
              <Input
                id="name"
                placeholder="Your display name in the party"
                value={name}
                onChange={(e) => setName(e.target.value)}
                disabled={isAutoJoining}
              />
            </div>
            <div className="items-top flex space-x-2">
              <Checkbox
                id="host"
                checked={isHost}
                onCheckedChange={(checked: CheckedState) =>
                  setIsHost(checked === "indeterminate" ? false : checked)
                }
                disabled={isAutoJoining}
              />
              <div className="grid gap-1.5 leading-none">
                <label
                  htmlFor="host"
                  className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                >
                  Party host
                </label>
              </div>
            </div>
          </CardContent>
          <CardFooter className="flex justify-center">
            <Button className="w-full" disabled={isAutoJoining}>
              {isAutoJoining ? "Joining..." : "Join"}
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
