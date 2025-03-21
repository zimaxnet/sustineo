import { useState, useEffect } from "react";
import { WEB_ENDPOINT } from "store/endpoint";

export interface User {
  name: string;
  email: string;
  avatar?: string;
}

const availableUsers: { [key: string]: string } = {
  "asha-sharma": "/images/people/asha-sharma.jpg",
  "louise-han": "/images/people/louise-han.jpg",
  "marco-casalaina": "/images/people/marco-casalaina.jpg",
  "seth-juarez": "/images/people/seth-juarez.jpg",
  "yina-arenas": "/images/people/yina-arenas.jpg",
  "zia-mansoor": "/images/people/zia-mansoor.jpg",
};

const defaultUser: User = {
  name: "Sara Lee",
  email: "sara.lee@microsoft.com",
};

const getUser = async (): Promise<User> => {
  if (WEB_ENDPOINT.startsWith("http://localhost")) {
    return defaultUser;
  }
  const response = await fetch(`${WEB_ENDPOINT}/.auth/me`);
  if (!response.ok) {
    return defaultUser;
  }
  const userData = await response.json();
  const email: string = userData[0].user_id;
  const name: string = userData[0].user_claims
    .find((claim: any) => claim.typ === "name")
    ?.val.toString();
  const nameKey: string = name.toLowerCase().replace(/\s/g, "-");
  const userAvatar = availableUsers[nameKey];
  if (userAvatar) {
    return {
      name: name,
      email: email,
      avatar: userAvatar,
    };
  } else {
    return {
      name: userData.name,
      email: userData.email,
    };
  }
};

/**
 * React hook for fetching and managing user data
 */
export const useUser = () => {
  const [user, setUser] = useState<User>({
    name: "",
    email: ""
  });
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchUser = async () => {
      setLoading(true);
      try {
        const userData = await getUser();
        setUser(userData);
      } catch (err) {
        setError(err as Error);
        setLoading(false);
        // on error, set user to default user
        setUser(defaultUser);
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, []);

  return [user, loading, error] as const;
};

export default useUser;
