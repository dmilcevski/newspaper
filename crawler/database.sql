--
-- PostgreSQL database dump
--

-- Dumped from database version 9.2.4
-- Dumped by pg_dump version 10.1

-- Started on 2018-04-04 16:33:05 CEST

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- TOC entry 1 (class 3079 OID 11751)
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- TOC entry 2187 (class 0 OID 0)
-- Dependencies: 1
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;



--
-- TOC entry 198 (class 1259 OID 328959535)
-- Name: annotated_news_article; Type: TABLE; Schema: public; 
--

CREATE TABLE annotated_news_article (
    news_article_id bigint NOT NULL,
    news_source_id bigint NOT NULL,
    processed_date timestamp(6) without time zone,
    matches json,
    entities json,
    facts json,
    types json
);


--
-- TOC entry 199 (class 1259 OID 328969778)
-- Name: annotation_error; Type: TABLE; Schema: public; 
--

CREATE TABLE annotation_error (
    news_article_id bigint NOT NULL,
    news_source_id bigint NOT NULL,
    error_message text,
    "timestamp" timestamp(6) without time zone
);

--
-- TOC entry 196 (class 1259 OID 327304955)
-- Name: news_article; Type: TABLE; Schema: public; 
--

CREATE TABLE news_article (
    id bigint NOT NULL,
    title character varying,
    url character varying,
    image_url character varying,
    text text,
    language character varying,
    crawl_date timestamp without time zone,
    publish_date timestamp(6) without time zone,
    news_source_id integer NOT NULL,
    authors character varying
);

--
-- TOC entry 195 (class 1259 OID 327304953)
-- Name: news_article_id_seq; Type: SEQUENCE; Schema: public; 
--

CREATE SEQUENCE news_article_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 2191 (class 0 OID 0)
-- Dependencies: 195
-- Name: news_article_id_seq; Type: SEQUENCE OWNED BY; Schema: public; 
--

ALTER SEQUENCE news_article_id_seq OWNED BY news_article.id;


--
-- TOC entry 194 (class 1259 OID 327302743)
-- Name: news_source; Type: TABLE; Schema: public; 
--

CREATE TABLE news_source (
    id bigint NOT NULL,
    url character varying(256) NOT NULL,
    domain character varying(256),
    brand character varying(256) NOT NULL,
    description character varying(2048),
    logo_url character varying(256),
    language character varying(45) DEFAULT 'en'::character varying NOT NULL
);


--
-- TOC entry 193 (class 1259 OID 327302741)
-- Name: news_source_id_seq; Type: SEQUENCE; Schema: public; 
--

CREATE SEQUENCE news_source_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 2192 (class 0 OID 0)
-- Dependencies: 193
-- Name: news_source_id_seq; Type: SEQUENCE OWNED BY; Schema: public; 
--

ALTER SEQUENCE news_source_id_seq OWNED BY news_source.id;

--
-- TOC entry 200 (class 1259 OID 352340692)
-- Name: translation_error; Type: TABLE; Schema: public; 
--

CREATE TABLE translation_error (
    news_article_id bigint NOT NULL,
    news_source_id bigint NOT NULL,
    error_message text,
    "timestamp" timestamp(6) without time zone
);


--
-- TOC entry 1971 (class 2604 OID 327304958)
-- Name: news_article id; Type: DEFAULT; Schema: public; 
--

ALTER TABLE ONLY news_article ALTER COLUMN id SET DEFAULT nextval('news_article_id_seq'::regclass);


--
-- TOC entry 1969 (class 2604 OID 327302746)
-- Name: news_source id; Type: DEFAULT; Schema: public; 
--

ALTER TABLE ONLY news_source ALTER COLUMN id SET DEFAULT nextval('news_source_id_seq'::regclass);


--
-- TOC entry 2043 (class 2606 OID 328959542)
-- Name: annotated_news_article annotated_news_article_pkey; Type: CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY annotated_news_article
    ADD CONSTRAINT annotated_news_article_pkey PRIMARY KEY (news_article_id, news_source_id);


--
-- TOC entry 2046 (class 2606 OID 328969785)
-- Name: annotation_error annotation_error_pkey; Type: CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY annotation_error
    ADD CONSTRAINT annotation_error_pkey PRIMARY KEY (news_article_id, news_source_id);



--
-- TOC entry 2038 (class 2606 OID 328936052)
-- Name: news_article news_article_pkey; Type: CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY news_article
    ADD CONSTRAINT news_article_pkey PRIMARY KEY (id, news_source_id);


--
-- TOC entry 2040 (class 2606 OID 328503581)
-- Name: news_article news_article_title_pubdate_news_source_language; Type: CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY news_article
    ADD CONSTRAINT news_article_title_pubdate_news_source_language UNIQUE (title, publish_date, news_source_id, language);


--
-- TOC entry 2033 (class 2606 OID 327302752)
-- Name: news_source news_source_pkey; Type: CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY news_source
    ADD CONSTRAINT news_source_pkey PRIMARY KEY (id);


--
-- TOC entry 2035 (class 2606 OID 327302754)
-- Name: news_source news_source_url_unq; Type: CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY news_source
    ADD CONSTRAINT news_source_url_unq UNIQUE (url);


--
-- TOC entry 2050 (class 2606 OID 352340700)
-- Name: translation_error translation_error_pkey; Type: CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY translation_error
    ADD CONSTRAINT translation_error_pkey PRIMARY KEY (news_article_id, news_source_id);



--
-- TOC entry 2031 (class 1259 OID 324239935)
-- Name: fk_annotated_document_document_idx; Type: INDEX; Schema: public; 
--

CREATE INDEX fk_annotated_document_document_idx ON annotated_document USING btree (document_id);


--
-- TOC entry 2044 (class 1259 OID 328969717)
-- Name: fk_annotated_news_article_news_article_idx; Type: INDEX; Schema: public; 
--

CREATE INDEX fk_annotated_news_article_news_article_idx ON annotated_news_article USING btree (news_article_id, news_source_id);


--
-- TOC entry 2047 (class 1259 OID 328969791)
-- Name: fk_annotation_error_news_article_idx; Type: INDEX; Schema: public; 
--

CREATE INDEX fk_annotation_error_news_article_idx ON annotation_error USING btree (news_article_id, news_source_id);


--
-- TOC entry 2048 (class 1259 OID 352340837)
-- Name: fk_translation_error_news_article_idx; Type: INDEX; Schema: public; 
--

CREATE INDEX fk_translation_error_news_article_idx ON annotation_error USING btree (news_article_id, news_source_id);


--
-- TOC entry 2036 (class 1259 OID 328842529)
-- Name: news_article_language; Type: INDEX; Schema: public; 
--

CREATE INDEX news_article_language ON news_article USING btree (language);


--
-- TOC entry 2041 (class 1259 OID 328842530)
-- Name: news_article_url; Type: INDEX; Schema: public; 
--

CREATE INDEX news_article_url ON news_article USING btree (url);


--
-- TOC entry 2071 (class 2606 OID 328959543)
-- Name: annotated_news_article fk_annotated_news_article_news_article; Type: FK CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY annotated_news_article
    ADD CONSTRAINT fk_annotated_news_article_news_article FOREIGN KEY (news_source_id, news_article_id) REFERENCES news_article(news_source_id, id);


--
-- TOC entry 2072 (class 2606 OID 328969786)
-- Name: annotation_error fk_annotation_error_article_news_article; Type: FK CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY annotation_error
    ADD CONSTRAINT fk_annotation_error_article_news_article FOREIGN KEY (news_source_id, news_article_id) REFERENCES news_article(news_source_id, id);


--
-- TOC entry 2070 (class 2606 OID 327304966)
-- Name: news_article fk_news_article_news_source; Type: FK CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY news_article
    ADD CONSTRAINT fk_news_article_news_source FOREIGN KEY (news_source_id) REFERENCES news_source(id);


--
-- TOC entry 2073 (class 2606 OID 352340701)
-- Name: translation_error fk_translation_error_article_news_article; Type: FK CONSTRAINT; Schema: public; 
--

ALTER TABLE ONLY translation_error
    ADD CONSTRAINT fk_translation_error_article_news_article FOREIGN KEY (news_source_id, news_article_id) REFERENCES news_article(news_source_id, id);



--
-- TOC entry 2055 (class 0 OID 0)
-- Dependencies: 193
-- Name: news_source_id_seq; Type: SEQUENCE SET; Schema: public; Owner: avdocuments
--

SELECT pg_catalog.setval('news_source_id_seq', 344, true);

-- Completed on 2018-04-04 16:25:50 CEST

--
-- PostgreSQL database dump complete
--

