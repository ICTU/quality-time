import { useEffect, useRef, useState } from 'react';

export const useBoundingBox = () => {
    const ref = useRef();
    const [boundingBox, setBoundingBox] = useState({});

    const set = () => setBoundingBox(ref?.current?.getBoundingClientRect() ?? {});

    useEffect(() => {
        set();
        window.addEventListener('resize', set);
        return () => window.removeEventListener('resize', set);
    }, []);

    return [boundingBox, ref];
};
