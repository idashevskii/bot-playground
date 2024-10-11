SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: schema_migrations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.schema_migrations (
    version character varying(128) NOT NULL
);


--
-- Name: stage; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.stage (
    title character varying,
    world_id integer,
    id integer NOT NULL,
    code character varying
);


--
-- Name: stage_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.stage_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: stage_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.stage_id_seq OWNED BY public.stage.id;


--
-- Name: step; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.step (
    stage_id integer,
    state text,
    actions text,
    logs text,
    interactions text,
    id integer NOT NULL
);


--
-- Name: step_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.step_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: step_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.step_id_seq OWNED BY public.step.id;


--
-- Name: world; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.world (
    title character varying,
    plugin character varying,
    config character varying,
    id integer NOT NULL
);


--
-- Name: world_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.world_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: world_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.world_id_seq OWNED BY public.world.id;


--
-- Name: stage id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stage ALTER COLUMN id SET DEFAULT nextval('public.stage_id_seq'::regclass);


--
-- Name: step id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.step ALTER COLUMN id SET DEFAULT nextval('public.step_id_seq'::regclass);


--
-- Name: world id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.world ALTER COLUMN id SET DEFAULT nextval('public.world_id_seq'::regclass);


--
-- Name: schema_migrations schema_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schema_migrations
    ADD CONSTRAINT schema_migrations_pkey PRIMARY KEY (version);


--
-- Name: stage stage_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stage
    ADD CONSTRAINT stage_pkey PRIMARY KEY (id);


--
-- Name: step step_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.step
    ADD CONSTRAINT step_pkey PRIMARY KEY (id);


--
-- Name: world world_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.world
    ADD CONSTRAINT world_pkey PRIMARY KEY (id);


--
-- Name: stage stage_world_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stage
    ADD CONSTRAINT stage_world_id_fkey FOREIGN KEY (world_id) REFERENCES public.world(id);


--
-- Name: step step_stage_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.step
    ADD CONSTRAINT step_stage_id_fkey FOREIGN KEY (stage_id) REFERENCES public.stage(id);


--
-- PostgreSQL database dump complete
--


--
-- Dbmate schema migrations
--

INSERT INTO public.schema_migrations (version) VALUES
    ('19990101000000');
