-- upgrade --
CREATE TABLE IF NOT EXISTS "place" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(250) NOT NULL,
    "point" GEOMETRY(POINT) NOT NULL
);
CREATE TABLE IF NOT EXISTS "region" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(250) NOT NULL,
    "poly" GEOMETRY(POLYGON) NOT NULL
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(20) NOT NULL,
    "content" JSONB NOT NULL
);
